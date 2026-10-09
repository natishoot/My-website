<?php
// Formulaire « Demander un devis » : envoie la demande par e-mail à NatiShoot (hébergement o2switch).
// Réponse JSON : {"ok":true} ou {"ok":false,"error":"..."}.

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

const DESTINATAIRE = 'contact@natishoot.fr';
const EXPEDITEUR = 'contact@natishoot.fr';

function reponse($ok, $code = 200, $erreur = '') {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $erreur]);
    exit;
}

function champ($nom, $max = 200) {
    $v = isset($_POST[$nom]) ? trim((string) $_POST[$nom]) : '';
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') reponse(false, 405, 'Méthode non autorisée');

// Piège à robots : ce champ invisible doit rester vide.
if (champ('bot-field') !== '') reponse(true);

$nom = champ('nom', 120);
$email = champ('email', 160);
$type = champ('type', 80);
$date = champ('date', 20);
$lieu = champ('lieu', 160);
$tel = champ('telephone', 40);
$message = champ('message', 5000);

if ($nom === '' || $type === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reponse(false, 400, 'Champs obligatoires manquants ou e-mail invalide');
}
// Pas de retour à la ligne dans les champs utilisés en en-tête (anti-injection).
$nom = str_replace("\n", ' ', $nom);
$type = str_replace("\n", ' ', $type);

$sujet = 'Demande de devis — ' . $type;
$corps = "Nouvelle demande reçue depuis natishoot.fr\n\n"
    . "Nom : $nom\n"
    . "E-mail : $email\n"
    . "Téléphone : " . ($tel !== '' ? $tel : '—') . "\n"
    . "Type de séance : $type\n"
    . "Date souhaitée : " . ($date !== '' ? $date : '—') . "\n"
    . "Lieu : " . ($lieu !== '' ? $lieu : '—') . "\n\n"
    . "Message :\n$message\n";

$entetes = [
    'From: ' . mb_encode_mimeheader('NatiShoot (site)', 'UTF-8') . ' <' . EXPEDITEUR . '>',
    'Reply-To: ' . mb_encode_mimeheader($nom, 'UTF-8') . ' <' . $email . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];

$ok = mail(DESTINATAIRE, mb_encode_mimeheader($sujet, 'UTF-8'), $corps, implode("\r\n", $entetes), '-f' . EXPEDITEUR);
$ok ? reponse(true) : reponse(false, 500, "L'envoi a échoué");
