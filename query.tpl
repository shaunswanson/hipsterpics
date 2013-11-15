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
            <center>
            <h1>Enter your favorite activity.</h1>
            <h3>(let's see how the hipsters have ruined it):</h3>
            </center>
            <div class="query_input">
            <form method="POST" class="form" action="/query">
                <center>
                <input type="text" name="query"/>
                <input type="submit" value="Submit"/>
                </center>
            </form>
            </div>
            <center>
            <br><br>
            <h5>Note: the database is a bit sparse right now.</h5>
            <h6>Some fun queries to try:</h6>
            <h6>
            XXX<br>
            XXX<br>
            XXX
            </h6>
            </center>
            <center>
            <h1>Would you like to hire me for a machine learning role?</h1>
            <h3>Check out my <a href="/resume">resume</a>.</h3>
            <h3>Email me <a href="mailto:shaun.swanson@ayloo.net">here</a>.</h3>
            <h1>This project is opensource.</h1>
            <h3>Feel free to contribute via <a href="https://github.com/drProton/hipsterpics/">Github</a>.</h3>
            </center>
        </div>
    </body>
</html>
