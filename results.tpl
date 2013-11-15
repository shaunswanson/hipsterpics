<!DOCTYPE html>
<html>
    <head>
        <title>enjoy.</title>
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        <style type="text/css">
            body {font-family:sans-serif;color:#4f494f;}
            form input {border-radius: 7.5px;}
            h5 {display: inline;}
            .label {text-align: right}
            .guestbook {float:left; padding-top: 10px;}
            .name {width:100%;float:left;padding:3px;}
            .wrapper {padding-left: 25px; padding-top: 20px}
            .btn {display: inline-block; background-color:#ccc; padding: 5px 10px; border-radius: 5px; border: outset 2px #ccc; color: #000; text-decoration: none; font-size: 12px;}
            .btn:active { 
                border: inset 2px #ccc;
            }
        </style>
    <script>
    
    function trainnetworkandredirect(url)
    {   
        alert("calling function");
        // (TODO) train network with winner chosen
        $.ajax({
            url: "/trainquery",
            data: {
                winnerurl: url
            },
            type: "get",
            contentType: "application/xml; charset = utf-8",
            success: function(data) {
                console.log(data);
            }
        });
        // alert("Thanks for voting!");
        // window.location = "http://localhost:8082/"

    }
    </script>
    </head>

    <body>
        <div class="wrapper">
            <h1><center>Help me learn!</center></h1>
            <div class="results">
                <center>
                Click the most hipster-looking picture related to&nbsp;&ldquo;
                %for word in words:
                {{word}}&nbsp;
                %end
                &rdquo;
                <br><br>
                %i = 0
                %for url in urls:
                %if i==0:
                <table border="0">
                <tr>
                %end      
                <div class="result">
                    <td>
                    <a href="/trainquery?winnerurl={{!url}}"><img src={{url}} width=250 height=250></a>
                    </td>         
                </div>
                %if i%2!=0 and i != len(urls)-1:
                </tr><tr>
                %end 
                %if i == len(urls)-1:
                </tr>
                %end
                %i += 1
                %end
                </center>
                %if len(urls) == 0:
                <center>
                ..oops. No results.
                <br>
                <a href="/">Please try again</a>
                </center>
                %end
            </div>
        </div>
    </body>
</html>
