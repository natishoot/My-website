#!/bin/sh
# Met en ligne natishoot.fr sur o2switch (SSH, clé ~/.ssh/natishoot_o2switch).
# Usage, depuis la racine du dépôt :  sh tools/deploy.sh          (envoi réel)
#                                     sh tools/deploy.sh --dry-run (simulation)
# Le site va dans public_html ; la clé secrète et les photos privées de la galerie
# vont un niveau au-dessus (/home/cilo1172), hors du web.
set -e
cd "$(dirname "$0")/.."
HOST=cilo1172@muguet.o2switch.net
SSH="ssh -i $HOME/.ssh/natishoot_o2switch -o IdentitiesOnly=yes"
PRIVE="$(cd .. && pwd)"

rsync -rlptz --delete $1 -e "$SSH" \
  --filter 'P cgi-bin/' --filter 'P .well-known/' \
  --exclude '.git/' --exclude '.gitignore' --exclude '.DS_Store' --exclude 'tools/' \
  --exclude 'README.md' --exclude 'netlify.toml' --exclude 'google*.html' \
  ./ "$HOST:public_html/"

rsync -rlptz --delete $1 -e "$SSH" --exclude '.DS_Store' \
  "$PRIVE/natishoot-galerie-privee/" "$HOST:natishoot-galerie-privee/"
rsync -ptz $1 -e "$SSH" "$PRIVE/natishoot-config.php" "$HOST:natishoot-config.php"
[ -z "$1" ] && $SSH $HOST 'find public_html -mindepth 1 -path public_html/cgi-bin -prune -o -type d -exec chmod 755 {} + -o -type f -exec chmod 644 {} +; chmod 700 natishoot-galerie-privee; chmod 600 natishoot-galerie-privee/* natishoot-config.php'
echo "Envoi terminé${1:+ (simulation)}."
