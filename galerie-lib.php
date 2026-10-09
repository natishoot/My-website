<?php
// Galerie privée Boudoir & nu : fonctions communes (codes d'accès signés, session).
// Un code a la forme NU-AAAAMMJJ-XXXX-YYYYYY : date de fin de validité, partie aléatoire, signature.
// Il est généré par tools/code_galerie.py avec la même clé secrète que le serveur.

require dirname(__DIR__) . '/natishoot-config.php';

header('X-Robots-Tag: noindex, nofollow');

function galerie_signature($base) {
    $alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    $h = hash_hmac('sha256', $base, GALERIE_SECRET, true);
    $out = '';
    for ($i = 0; $i < 6; $i++) $out .= $alphabet[ord($h[$i]) % 32];
    return $out;
}

// Renvoie l'horodatage de fin de validité si le code est valable, sinon false.
function galerie_verifier_code($code) {
    $code = strtoupper(trim($code));
    if (!preg_match('/^NU-(\d{8})-([A-Z2-9]{4})-([A-Z2-9]{6})$/', $code, $m)) return false;
    $base = "NU-$m[1]-$m[2]";
    if (!hash_equals(galerie_signature($base), $m[3])) return false;
    $fin = DateTime::createFromFormat('Ymd H:i:s', $m[1] . ' 23:59:59', new DateTimeZone('Europe/Paris'));
    if (!$fin || $fin->getTimestamp() < time()) return false;
    return $fin->getTimestamp();
}

function galerie_session() {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => !empty($_SERVER['HTTPS']), 'httponly' => true, 'samesite' => 'Strict']);
        session_name('natigal');
        session_start();
    }
}

function galerie_acces_ouvert() {
    galerie_session();
    return !empty($_SESSION['galerie_fin']) && $_SESSION['galerie_fin'] >= time();
}

// Photos : boudoir-NN.jpg (grand format) et boudoir-NN-900.jpg (vignette), dans le dossier privé.
function galerie_photos() {
    $liste = glob(GALERIE_PHOTOS . '/boudoir-[0-9][0-9].jpg') ?: [];
    sort($liste);
    return array_map('basename', $liste);
}
