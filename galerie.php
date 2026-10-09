<?php
// Galerie privée Boudoir & nu : accès par code valable 7 jours (voir tools/code_galerie.py).
require __DIR__ . '/galerie-lib.php';
galerie_session();

$erreur = '';
if (isset($_GET['sortir'])) {
    $_SESSION = [];
    session_destroy();
    header('Location: galerie.php');
    exit;
}
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $_SESSION['essais'] = ($_SESSION['essais'] ?? 0) + 1;
    if ($_SESSION['essais'] > 8) {
        $erreur = 'Trop de tentatives. Réessayez plus tard ou écrivez-moi.';
    } elseif ($fin = galerie_verifier_code($_POST['code'] ?? '')) {
        session_regenerate_id(true);
        $_SESSION['galerie_fin'] = $fin;
        $_SESSION['essais'] = 0;
        header('Location: galerie.php');
        exit;
    } else {
        usleep(600000);
        $erreur = 'Ce code n’est pas valable ou a expiré.';
    }
}
$ouvert = galerie_acces_ouvert();
$v = substr(md5_file(__DIR__ . '/assets/pages.css') . md5_file(__DIR__ . '/assets/pages.js'), 0, 8);
?><!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Galerie privée — NatiShoot</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0b0a09">
<meta name="color-scheme" content="dark">
<link rel="preload" href="fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="stylesheet" href="assets/pages.css?v=<?= $v ?>">
</head>
<body>
<header class="nav">
  <a class="logo" href="index.html">NATISHOOT <small>photography</small></a>
  <a class="back" href="index.html">← Retour à l’accueil</a>
  <?php if ($ouvert): ?><a class="btn" href="galerie.php?sortir">Fermer la galerie</a><?php endif; ?>
</header>
<main>
<?php if (!$ouvert): ?>
<section class="legal gal-code">
  <div class="eyebrow">Galerie privée</div>
  <h1>Boudoir <em>&amp; nu</em></h1>
  <p>Cette galerie est réservée aux personnes qui ont reçu un code d’accès. Le code est valable 7 jours.</p>
  <form method="post" class="gal-form" autocomplete="off">
    <label for="code">Votre code d’accès</label>
    <input id="code" name="code" required placeholder="NU-AAAAMMJJ-XXXX-XXXXXX" spellcheck="false" autocapitalize="characters">
    <button class="btn solid" type="submit">Ouvrir la galerie →</button>
    <?php if ($erreur): ?><p class="gal-err" role="alert"><?= htmlspecialchars($erreur) ?></p><?php endif; ?>
  </form>
  <p class="note">Pas encore de code ? <a href="index.html#series">Demandez l’accès</a> depuis la carte « Boudoir &amp; nu » de l’accueil.</p>
</section>
<?php else: $photos = galerie_photos(); ?>
<section class="head">
  <div><div class="eyebrow">Galerie privée</div><h1>Boudoir <em>&amp; nu</em></h1></div>
  <div><p class="lead">Accès ouvert jusqu’au <?= date('d/m/Y', $_SESSION['galerie_fin']) ?>. Ces images sont strictement personnelles : merci de ne pas les copier ni les partager.</p>
  <div class="meta"><div><b><?= count($photos) ?></b><span class="mono">photos</span></div></div></div>
</section>
<div class="grid">
<?php foreach ($photos as $p): $n = substr($p, 0, -4); $t = GALERIE_PHOTOS . "/$n-900.jpg"; [$w, $h] = is_file($t) ? getimagesize($t) : [900, 1125]; ?>
  <a class="tile reveal" href="photo.php?f=<?= $p ?>" data-alt="Boudoir &amp; nu — NatiShoot"><img src="photo.php?f=<?= $n ?>-900.jpg" width="<?= $w ?>" height="<?= $h ?>" alt="Boudoir &amp; nu — photographie NatiShoot" loading="lazy" decoding="async"></a>
<?php endforeach; ?>
</div>
<section class="band"><p>Merci pour <em>votre confiance</em></p><a class="btn" href="galerie.php?sortir">Fermer la galerie →</a></section>
<?php endif; ?>
</main>
<footer>
  <div class="bot">
    <span>© 2026 NatiShoot Photography — Patrick Rhino EI · SIRET 531 577 955 00036 · TVA non applicable, art. 293 B du CGI</span>
    <span><a href="https://instagram.com/tfl.971" target="_blank" rel="noopener">Instagram</a> · <a href="mentions-legales.html">Mentions légales</a> · <a href="cgv.html">CGV</a></span>
  </div>
</footer>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Visionneuse">
  <header><span class="mono" id="lbc"></span><button class="x" id="lbx" aria-label="Fermer">✕</button></header>
  <div class="stage"><img id="lbi" alt=""></div>
  <div class="foot"><span class="mono" id="lbt"></span><div class="arrows"><button id="lbp" aria-label="Précédente">←</button><button id="lbn" aria-label="Suivante">→</button></div></div>
</div>
<script src="assets/pages.js?v=<?= $v ?>" defer></script>
</body>
</html>
