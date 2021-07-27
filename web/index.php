<html>

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
</head>

<body>

    <h4>Python Library</h4>
    <ul>
        <li>
            <a href="pip/list.php">pip list</a>
        </li>
        <li><a href="pip/install.php">pip install ...</a></li>
    </ul>

    <hr>

    <h4>Databases (Admin)</h4>
    <ul>
        <li>
            <a href="http://localhost:8081">phpmyadmin (MariaDB)</a>
        </li>
        <li>install library tambahan python</li>
    </ul>

    <hr>

    <h4>Airflow</h4>
    <ul>
        <li>
            <a href="http://localhost:8080">Web Airflow</a>
        </li>
        
    </ul>





    <hr />

    <h4>Status</h4>
    <?php

    // $output = shell_exec('pip3 list');
    // echo "<pre>$output</pre>";

    $string = file_get_contents("status.js");
    $json_a = json_decode($string, true);

    foreach ($json_a as $key => $value) {
        echo  $key . ':' . $value;
    }

    ?>

</body>

</html>