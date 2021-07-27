<html>

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
</head>

<body>

    <?php

    $lib = addslashes($_POST["library"]);

    $output = shell_exec("pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install $lib");
    echo "<pre>$output</pre>";

    ?>

</body>

</html>