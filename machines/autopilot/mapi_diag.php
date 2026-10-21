<?php
header('Content-Type: text/plain; charset=UTF-8');

echo "PHP SAPI: ", PHP_SAPI, "\n";
echo "MAPI loaded: ",
     extension_loaded('mapi') ? 'yes' : 'no',
     "\n";

if (extension_loaded('mapi')) {
    $functions = get_extension_funcs('mapi');

    echo "MAPI function count: ",
         count($functions ?: []),
         "\n";

    foreach ($functions ?: [] as $function) {
        echo $function, "\n";
    }
}
