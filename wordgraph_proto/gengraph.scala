import java.io.PrintWriter

import scala.collection.JavaConverters._
import scala.collection.JavaConversions._

import java.io.File
import org.deeplearning4j.models.embeddings.loader.WordVectorSerializer
import org.deeplearning4j.models.word2vec.Word2Vec

import spray.json._
import DefaultJsonProtocol._

object sandbox {
	def main(args: Array[String]){

		val out1 = new PrintWriter("graph.json")
		val vec = WordVectorSerializer.readWord2VecModel(new File("vec.txt"))

		//引数単語の類似度25位～45位を取得（最上位はつまらない）
		val words1 = vec.wordsNearest(args(0), 45).takeRight(20).toSet

		var words2:Set[Object] = Set()

		//出力用配列、d3.js向け
		var nodes:List[Map[String,String]] = List()
		var links:List[Map[String,String]] = List()

		words1.foreach { w1 =>
			//グラフで使うためにsimilarityを保存しておく
			links :+= Map("source"->args(0),"target"->w1,"value"->vec.similarity(args(0),w1).toString)
			//類似度上位単語を入力に類似度上位単語をさらに検索する
			val word2p = vec.wordsNearest(w1,10)
			words2 ++= word2p
			word2p.foreach { w2 =>
				links :+= Map("source"->w1.toString,"target"->w2.toString,"value"->vec.similarity(w1.toString,w2.toString).toString)
			}
		}
		//結合して重複除去
		val words = words1 ++ words2 + args(0)
		//色分け用に深さ別にgroupを付与
		words.foreach { word =>
			if (args(0) == word) {
				nodes :+= Map("id"->word.toString, "group"->"1")
			} else if (words1(word.toString)) {
				nodes :+= Map("id"->word.toString, "group"->"2")
			} else {
				nodes :+= Map("id"->word.toString, "group"->"3")
			}
		}

//		下記コメントアウト箇所はsimilarity全探索版
//		var sims:Map[Set[String],Double] = Map()
//		words.foreach { A =>
//			words.foreach { B =>
//				if (A != B) {
//					val sim = vec.similarity(A.toString,B.toString)
//					if (sim >= 0.95) {
//						sims = sims + (Set(A.toString,B.toString)->sim)
//					}
//				}
//			}
//		}
//		sims.foreach { case(set,sim) =>
//			val list = set.toList
//			links :+= Map("source"->list(0),"target"->list(1),"value"->sim.toString)
//		}

		//JSON出力
		out1.write(Map(
			"nodes"->nodes,
			"links"->links
		).toJson.toString)
		
		out1.close

	}
}