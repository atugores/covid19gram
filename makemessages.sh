#
# Shell script to manage .po files.
#
# Adapted from: https://docs.plone.org/develop/plone/i18n/internationalisation.html
#

CATALOGNAME="messages"

# List of languages
LANGUAGES="en ca es it"

# Create locales folder structure for languages
install -d locales
for lang in $LANGUAGES; do
    install -d locales/$lang/LC_MESSAGES
done

I18NDUDE=i18ndude
VERIFI18NDUDE=`which $I18NDUDE`
if [ "$VERIFI18NDUDE" = "" ]; then
        echo "You must install i18ndude: pip install i18ndude"
        exit
fi

#
# Do we need to merge manual PO entries from a file called manual.pot.
# this option is later passed to i18ndude
#
if test -e locales/manual.pot; then
        echo "Manual PO entries detected"
        MERGE="--merge locales/manual.pot"
else
        echo "No manual PO entries detected"
        MERGE=""
fi

# Rebuild .pot
$I18NDUDE rebuild-pot --pot locales/$CATALOGNAME.pot $MERGE --create $CATALOGNAME *.py

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po
        # Create po file if not exists
        touch $PO
        # Sync po file
        echo "Syncing $PO"
        $I18NDUDE sync --pot locales/$CATALOGNAME.pot $PO
        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po
    fi
done
