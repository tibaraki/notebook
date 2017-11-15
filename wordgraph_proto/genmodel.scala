import java.io.PrintWriter
import java.io.StringReader
import javax.xml.xpath._
import org.xml.sax.InputSource
import org.w3c.dom.NodeList
import scala.collection.JavaConverters._
import scalaj.http._
import nu.validator.htmlparser.dom.HtmlDocumentBuilder

import org.atilika.kuromoji.Tokenizer
import org.atilika.kuromoji.Token
import scala.collection.JavaConversions._

import java.text.Normalizer
import scala.collection.mutable.Map

import java.io.File
import org.deeplearning4j.models.embeddings.loader.WordVectorSerializer
import org.deeplearning4j.models.word2vec.Word2Vec
import org.deeplearning4j.text.sentenceiterator.LineSentenceIterator
import org.deeplearning4j.text.sentenceiterator.SentenceIterator
import org.deeplearning4j.text.sentenceiterator.SentencePreProcessor
import org.deeplearning4j.text.tokenization.tokenizer.TokenPreProcess
import org.deeplearning4j.text.tokenization.tokenizer.preprocessor.EndingPreProcessor
import org.deeplearning4j.text.tokenization.tokenizerfactory.DefaultTokenizerFactory
import org.deeplearning4j.text.tokenization.tokenizerfactory.TokenizerFactory

object sandbox{
	def main(args: Array[String]){

		val out1 = new PrintWriter("rawhtml.txt")
		val out2 = new PrintWriter("rawtext.txt")
		val out3 = new PrintWriter("wordlist.txt")
		val out4 = new PrintWriter("wordcount.txt")

		val words = new StringBuilder()

		var wordcount = Map[String,Int]()
		
		for (page <- 0 until args(1).toInt) {
			val body = Http("https://www.google.co.jp/search").params(Seq("q"->args(0),"tbm"->"nws","start"->(page*10).toString)).asString.body
			out1.write(body)
			
			val builder = new HtmlDocumentBuilder
			
			val dom = builder.parse(new InputSource(new StringReader(body.replaceAll("</*b>","").replaceAll("""&nbsp;\.\.\.""",""))))
			val xpath = XPathFactory.newInstance.newXPath
			
			val nodelist = xpath.evaluate("//*[@class='st']/text()",dom,XPathConstants.NODESET).asInstanceOf[NodeList]

			val tokenizer = Tokenizer.builder.mode(Tokenizer.Mode.NORMAL).build

			for (i <- 0 until nodelist.getLength) {
				out2.write(nodelist.item(i).getNodeValue + "\n\n")
				val tokens = tokenizer.tokenize(nodelist.item(i).getNodeValue)
				tokens.foreach { token =>
					if (token.getAllFeatures().indexOf("名詞") != -1) {
						//全半角の統一、全角記号一部除去
						val word = Normalizer.normalize(token.getSurfaceForm(), Normalizer.Form.NFKC).replaceAll("[、。（）「」]","")
						//以下の単語を除外：記号のみ、数字のみ、1文字のみ、ひらがなのみ2文字、年月日表現、曜日表現
						if (!word.matches("""([ -\/:-@\[-`\{-\~]+|\d+|.|[\u3041-\u3096]{2}|[0-9月日ヶカ箇ヵ週年]+|[月火水木金土日曜]+)""")) {
							words.append(word)
							words.append(" ")
							
							if (wordcount.contains(word)) {
								wordcount.update(word, wordcount(word)+1)
							} else {
								wordcount += (word -> 1)
							}
						}
					}
			    }
				words.append("\n")
			}
			//DOS攻撃にならないように気を遣いましょう
			Thread.sleep(1500)
		}

		out3.write(words.toString)
		
		out4.write(wordcount.toSeq.sortWith((a,b) => a._2>b._2).toString)
		
		out1.close
		out2.close
		out3.close
		out4.close

		//Word2vecへの投入
		
		val fileiterator = new LineSentenceIterator(new File("wordlist.txt"))
		val d4jtokenizer = new DefaultTokenizerFactory()
		
		val vec = new Word2Vec.Builder()
			.batchSize(1000)	// ミニバッチのサイズ
			.minWordFrequency(1)	// 単語の最低出現回数。ここで指定した回数以下の出現回数の単語は学習から除外される
			.useAdaGrad(false)	// AdaGradを利用するかどうか
			.layerSize(100)	// 単語ベクトルの次元数
			.iterations(3)	// 学習時の反復回数
			.learningRate(0.025)	// 学習率
			.minLearningRate(1e-3)	// 学習率の最低値
			.negativeSample(10)
			.iterate(fileiterator)	// 文章データクラス
			.tokenizerFactory(d4jtokenizer)	// 単語分解クラス
			.build()
			
		vec.fit()

		WordVectorSerializer.writeWordVectors(vec,"vec.txt")
		
		val similar10 = vec.wordsNearest(args(0), 20)
		val resfile = new PrintWriter("similar.txt")
		similar10.foreach { word =>
			resfile.write(word)
			resfile.write("\n")
		}
		resfile.close

	}
}