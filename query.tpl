<!DOCTYPE html>
<html>
    <head>
        <title>Hmm..</title>
        <style type="text/css">
            body {font-family:sans-serif;color:#4f494f;}
            form input {border-radius: 7.5px;}
            h5 {display: inline;}
            .label {text-align: right}
            .guestbook {float:left; padding-top: 10px;}
            .name {width:100%;float:left;padding:3px;}
            .wrapper {padding-left: 25px; padding-top: 20px}
        </style>
    </head>

    <body>
        <div class="wrapper">
            <h1><center>Ask and ye shall receive:</center></h1>
            <div class="query_input">
            <form method="POST" class="form" action="/query">
                <center>
                <input type="text" name="query"/>
                <input type="submit" value="I can haz?"/>
                </center>
            </form>
            </div>
        </div>
    </body>
</html>
