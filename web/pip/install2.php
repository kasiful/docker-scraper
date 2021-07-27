<html>

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
</head>

<body>

    <?php
    
    $lib = addslashes($_POST["library"]);
    $legal = $lib == str_replace(array( ';','&&','||'), ' ', $lib) ? true:false;

    if($legal) {
        $output = shell_exec("pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install ".$lib);
        echo "<pre>$output</pre>";
    }
    else{
        echo 'Gotcha, You trying something bad :) ';
    }
    
    ?>
    
</body>

</html>