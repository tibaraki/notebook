## 使用ツール

# LogParsar
#  https://www.microsoft.com/ja-jp/download/details.aspx?id=24659
# LogParsar Studio(LPSV)
#  https://gallery.technet.microsoft.com/Log-Parser-Studio-cd458765

## 参照するログファイル。LPSVと同フォルダに置く

# AD及び端末のSystem32\winevtから取得のこと
# System.evtx
# Security.evtx
# （使うかも）Microsoft-Windows-TaskScheduler%4Operational.evtx


## 元ネタ

# https://gist.github.com/exp0se/1bae653b790cf5571d20
# https://www.jpcert.or.jp/research/AD_report_20170314.pdf


## 使い方

# evtxファイルをLPSVフォルダに配置
# LPSV起動
# 新規クエリを開いて下記クエリから好きなものをコピペして実行




## event id 1102 イベントログの削除イベント

# Eventlog was cleared
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') as Username, EXTRACT_TOKEN(Strings, 2, '|') AS Workstation FROM 'Security.evtx' WHERE EventID = '1102'





## event id 4624 ログインの成功、GoldenTicket/SilverTicket使用調査 Domainに「eo.oe.kiwi:」があると攻撃ツールが特定できる

# IPやユーザに怪しいものがないか。ログオンタイプ3（=ネットワーク認証）4（=バッチスクリプト）5（=サービス）に注意

# successful logon
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType,EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY')

# Find specific user
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType,EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND Username = 'Administrator'

# Find RDP logons
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType,EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND LogonType = '10'

# Find console logons
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType,EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND LogonType = '2'

# Find specific IP
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType,EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND SourceIP = '10.1.47.151'


# look at NTLM based logons 
# possible pass-the-hash 
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType, EXTRACT_TOKEN(strings, 10, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND AuthPackage LIKE '%NtLmSsp%' AND Username NOT LIKE '%$'

# group by NTLM users
SELECT COUNT(*) AS CNT, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 8, '|') as LogonType, EXTRACT_TOKEN(strings, 9, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 11, '|') AS Workstation, EXTRACT_TOKEN(Strings, 17, '|') AS ProcessName, EXTRACT_TOKEN(Strings, 18, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND AuthPackage LIKE '%NtLmSsp%' AND Username NOT LIKE '%$' GROUP BY Username, Domain, LogonType, AuthPackage, Workstation, ProcessName, SourceIP ORDER BY CNT DESC


# group by users
SELECT EXTRACT_TOKEN(Strings, 5, '|') as Username, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Username NOT LIKE '%$' GROUP BY Username ORDER BY CNT DESC

# group by domain 
SELECT EXTRACT_TOKEN(Strings, 6, '|') as Domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 GROUP BY Domain ORDER BY CNT DESC

# group by authpackage
SELECT EXTRACT_TOKEN(Strings, 9, '|') as AuthPackage, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 GROUP BY AuthPackage ORDER BY CNT DESC

# group by LogonType
SELECT EXTRACT_TOKEN(Strings, 8, '|') as LogonType, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 GROUP BY LogonType ORDER BY CNT DESC

# group by workstation name 
SELECT EXTRACT_TOKEN(Strings, 11, '|') as Workstation, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 GROUP BY Workstation ORDER BY CNT DESC

# group by process name 
SELECT EXTRACT_TOKEN(Strings, 17, '|') as ProcName, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4624 GROUP BY ProcName ORDER BY CNT DESC







## event id 4625 ログインの失敗

# unsuccessful logon
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 10, '|') as LogonType,EXTRACT_TOKEN(strings, 11, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 13, '|') AS Workstation, EXTRACT_TOKEN(Strings, 19, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY')

# Find specific User
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 10, '|') as LogonType,EXTRACT_TOKEN(strings, 11, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 13, '|') AS Workstation, EXTRACT_TOKEN(Strings, 19, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND Username = 'Administrator'


# Find specific IP
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 10, '|') as LogonType,EXTRACT_TOKEN(strings, 11, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 13, '|') AS Workstation, EXTRACT_TOKEN(Strings, 19, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND SourceIP = '10.1.47.151'

# check ntlm based attempts
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 10, '|') as LogonType, EXTRACT_TOKEN(strings, 11, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 13, '|') AS Workstation, EXTRACT_TOKEN(Strings, 19, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND AuthPackage LIKE '%NtLmSsp%' AND Username NOT LIKE '%$'

# group by ntlm users
SELECT COUNT(*) AS CNT, EXTRACT_TOKEN(Strings, 5, '|') as Username, EXTRACT_TOKEN(Strings, 6, '|') as Domain, EXTRACT_TOKEN(Strings, 10, '|') as LogonType,EXTRACT_TOKEN(strings, 11, '|') AS AuthPackage, EXTRACT_TOKEN(Strings, 13, '|') AS Workstation, EXTRACT_TOKEN(Strings, 19, '|') AS SourceIP FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Domain NOT IN ('NT AUTHORITY') AND AuthPackage LIKE '%NtLmSsp%' AND Username NOT LIKE '%$' GROUP BY Username, Domain, LogonType, AuthPackage, Workstation, SourceIP ORDER BY CNT DESC

# group by Username
SELECT COUNT(*) AS CNT, EXTRACT_TOKEN(Strings, 5, '|') as Username FROM 'Security.evtx' WHERE EventID = 4625 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Username NOT LIKE '%$' GROUP BY Username ORDER BY CNT DESC





## event id 4688 【重要】プロセス作成。コマンドラインの実行履歴が見えるように改修要。Stringsそのまま見ればOK

# new process was created
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain, EXTRACT_TOKEN(Strings, 5, '|') AS Process FROM 'Security.evtx' WHERE EventID = 4688
# Search by user
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain, EXTRACT_TOKEN(Strings, 5, '|') AS Process FROM 'Security.evtx' WHERE EventID = 4688 AND Username = 'Administrator'
# Search by process name
SELECT TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain, EXTRACT_TOKEN(Strings, 5, '|') AS Process FROM 'Security.evtx' WHERE EventID = 4688 AND Process LIKE '%rundll32.exe%'
# group by username
SELECT COUNT(*) AS CNT, EXTRACT_TOKEN(Strings, 1, '|') AS Username FROM 'Security.evtx' WHERE EventID = 4688 GROUP BY Username ORDER BY CNT DESC
# group by process name
SELECT COUNT(*) AS CNT, EXTRACT_TOKEN(Strings, 5, '|') AS Process FROM 'Security.evtx' WHERE EventID = 4688 GROUP BY Process ORDER BY CNT DESC






## event id 5140 ファイル共有。SYSVOLやIPC以外の怪しげな共有パスが指定されていないか

# A network share object was accessed
SELECT * FROM 'Security.evtx' WHERE EventID = '5140'




## event id 7045 サービス作成イベント。怪しげなユーザ・プロセスがないか

# New Service was installed in system
Select TimeGenerated AS Date, extract_token(strings, 0, '|') AS ServiceName, extract_token(strings, 1, '|') AS ServicePath, extract_token(strings, 4, '|') AS ServiceUser FROM System.evtx WHERE EventID = 7045




## event id 4724 パスワードリセット

# attempt to reset user 
SELECT TimeGenerated AS Date, extract_token(strings, 0, '|') as user, extract_token(strings, 1, '|') as domain, extract_token(strings, 4, '|') as whichaccount, extract_token(strings, 5, '|') as whichdomain FROM 'Security.evtx' WHERE EventID = 4724





## event id 4738 ユーザ変更

# user account was changed 
SELECT TimeGenerated AS Date, extract_token(strings, 1, '|') as user, extract_token(strings, 2, '|') as domain, extract_token(strings, 5, '|') as whichaccount, extract_token(strings, 6, '|') as whichdomain FROM 'Security.evtx' WHERE EventID = 4738






## event id 4769 Kerberos認証(STリクエスト) MS14-068の攻撃調査 0xfが含まれる場合、攻撃有り。0x0が成功

# Kerberos Service ticket was requested
SELECT TimeGenerated AS Date, extract_token(strings, 0, '|') as user, extract_token(strings, 1, '|') as domain, extract_token(strings, 2, '|') as service, extract_token(strings, 5, '|') as cipher, extract_token(strings, 6, '|') as sourceip FROM 'Security.evtx' WHERE EventID = 4769

# group by user 
SELECT extract_token(strings, 0, '|') as user, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 AND user NOT LIKE '%$' GROUP BY user ORDER BY CNT DESC

# group by domain 
SELECT extract_token(strings, 1, '|') as domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY domain ORDER BY CNT DESC

# group by service
SELECT extract_token(strings, 2, '|') as service, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY service ORDER BY CNT DESC

# group by cipher
SELECT extract_token(strings, 5, '|') as cipher, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY cipher ORDER BY CNT DESC





## event id 4768 Kerberos認証(TGTリクエスト) 0x0が成功

# Kerberos TGT was requested
SELECT TimeGenerated AS Date, extract_token(strings, 0, '|') as user, extract_token(strings, 1, '|') as domain, extract_token(strings, 7, '|') as cipher, extract_token(strings, 9, '|') as sourceip FROM 'Security.evtx' WHERE EventID = 4768
# group by user 
SELECT extract_token(strings, 0, '|') as user, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4768 AND user NOT LIKE '%$' GROUP BY user ORDER BY CNT DESC
# group by domain
SELECT extract_token(strings, 1, '|') as domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4768 GROUP BY domain ORDER BY CNT DESC
# group by cipher
SELECT extract_token(strings, 7, '|') as cipher, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4768 GROUP BY cipher ORDER BY CNT DESC
# event id 4769
# Kerberos Service ticket was requested
SELECT TimeGenerated AS Date, extract_token(strings, 0, '|') as user, extract_token(strings, 1, '|') as domain, extract_token(strings, 2, '|') as service, extract_token(strings, 5, '|') as cipher, extract_token(strings, 6, '|') as sourceip FROM 'Security.evtx' WHERE EventID = 4769
# group by user 
SELECT extract_token(strings, 0, '|') as user, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 AND user NOT LIKE '%$' GROUP BY user ORDER BY CNT DESC
# group by domain 
SELECT extract_token(strings, 1, '|') as domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY domain ORDER BY CNT DESC
# group by service
SELECT extract_token(strings, 2, '|') as service, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY service ORDER BY CNT DESC
# group by cipher
SELECT extract_token(strings, 5, '|') as cipher, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4769 GROUP BY cipher ORDER BY CNT DESC







## event id 4776 NTLM認証。pass the hashの懸念

# domain/computer attemped to validate user credentials
Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain FROM 'Security.evtx' WHERE EventID = 4776 AND Domain NOT IN ('NT AUTHORITY') AND Username NOT LIKE '%$'
# Search by username
Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain FROM 'Security.evtx' WHERE EventID = 4776 AND Domain NOT IN ('NT AUTHORITY') AND Username NOT LIKE '%$' AND Username = 'Administrator'
# group by username
Select EXTRACT_TOKEN(Strings, 1, '|') AS Username, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4776 AND Username NOT LIKE '%$' GROUP BY Username ORDER BY CNT DESC
# group by domain 
Select EXTRACT_TOKEN(Strings, 2, '|') AS Domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4776 GROUP BY Domain ORDER BY CNT DESC






## event id 4672 特権の割り当て

# Admin logon
Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain FROM 'Security.evtx' WHERE EventID = 4672 AND Domain NOT IN ('NT AUTHORITY')
# Find specific user
Select TimeGenerated AS Date, EXTRACT_TOKEN(Strings, 1, '|') AS Username, EXTRACT_TOKEN(Strings, 2, '|') AS Domain FROM 'Security.evtx' WHERE EventID = 4672 AND Domain NOT IN ('NT AUTHORITY') AND Username = 'Administrator'
# group by username
Select EXTRACT_TOKEN(Strings, 1, '|') AS Username, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4672 AND Username NOT IN ('SYSTEM'; 'ANONYMOUS LOGON'; 'LOCAL SERVICE'; 'NETWORK SERVICE') AND Username NOT LIKE '%$' GROUP BY Username ORDER BY CNT DESC
# group by domain 
Select EXTRACT_TOKEN(Strings, 2, '|') AS Domain, COUNT(*) AS CNT FROM 'Security.evtx' WHERE EventID = 4672 AND Domain NOT IN ('NT AUTHORITY') GROUP BY Domain ORDER BY CNT DESC






## event id 4698 タスクの作成

# Windows\Tasks
# Windows\System32\Tasks
# も参照

SELECT TOP 10 * FROM '[LOGFILEPATH]' where EventID=4698




