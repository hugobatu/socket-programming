HTTP/1.1 200 OK
Server: nginx
Date: Sat, 12 Aug 2023 19:00:55 GMT
Content-Type: text/html; charset=UTF-8
Connection: close
Vary: Accept-Encoding
Vary: Accept-Encoding

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 2.0//EN">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<html>
<head>
	<title>FrogFind!</title>
</head>
<body>

    <br><br><center><h1><font size=7><font color="#008000">Frog</font>Find!</font></h1></center>
    <center><img src="/img/frogfind.gif" width="174" height="80" alt="a pixelated cartoon graphic of a fat, lazy, unamused frog with a keyboard in front of them, awaiting your search query"></center>
    <center><h3>The Search Engine for Vintage Computers</h3></center>
    <br><br>
    <center>
    <form action="/" method="get">
    Leap to: <input type="text" size="30" name="q"><br>
    <input type="submit" value="Ribbbit!">
    </center>
    <br><br><br>
    <small><center>Built by <b><a href="https://youtube.com/ActionRetro" target="_blank" rel="noopener">Action Retro</a></b> on YouTube | Logo by <b><a href="https://www.youtube.com/mac84"  target="_blank" rel="noopener">Mac84</a></b> | <a href="about.php">Why build such a thing?</a></center><br>
    <small><center>Powered by DuckDuckGo</center></small>
</form>

</body>
</html>