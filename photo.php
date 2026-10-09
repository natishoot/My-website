<?php
// Sert une photo de la galerie privée, uniquement avec un accès ouvert par un code valable.
require __DIR__ . '/galerie-lib.php';

$f = isset($_GET['f']) ? (string) $_GET['f'] : '';
if (!galerie_acces_ouvert() || !preg_match('/^boudoir-\d{2}(-900)?\.jpg$/', $f) || !is_file(GALERIE_PHOTOS . '/' . $f)) {
    http_response_code(404);
    exit;
}
header('Content-Type: image/jpeg');
header('Cache-Control: private, no-store');
header('Content-Length: ' . filesize(GALERIE_PHOTOS . '/' . $f));
readfile(GALERIE_PHOTOS . '/' . $f);
