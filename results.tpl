<!DOCTYPE html>
<html>
    <head>
        <title>enjoy.</title>
        <style type="text/css">
            body {font-family:sans-serif;color:#4f494f;}
            form input {border-radius: 7.5px;}
            h5 {display: inline;}
            .label {text-align: right}
            .guestbook {float:left; padding-top: 10px;}
            .name {width:100%;float:left;padding:3px;}
            .wrapper {padding-left: 25px; padding-top: 20px}
        </style>
    <script>
    function trainnetworkandredirect(words, urls, winnerindex)
    {
        // (TODO) train network with winner chosen
        $.ajax({
            url: "https://http://localhost:8080/trainquery"
            type: "get",
            contentType: "application/xml; charset = utf-8",
            success: trainquery(words,urls, urls[winnerindex])
        });
        alert("Thanks for voting!");
        window.location = "http://localhost:8082/"

    }
    </script>
    </head>

    <body>
        <div class="wrapper">
            <h1>Ah, that's the stuff.</h1>
            <div class="results">
                results for&nbsp;&ldquo;
                %for word in words:
                {{word}}&nbsp;
                %end
                &rdquo;
                <br><br>
                %i = 0
                %for url in urls:
                <div class="result">
                    <a href={{url}} target="_blank">{{url}}</a>
                    <button onclick="trainnetworkandredirect({{words}},{{urls}},{{i}})">WINNER</button>
                    <br><br>         
                </div>
                %i += 1
                %end
            </div>
        </div>
    </body>
</html>
