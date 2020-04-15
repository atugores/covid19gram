#
# Shell script to manage .po files.
#
# Adapted from: https://docs.plone.org/develop/plone/i18n/internationalisation.html
#

CATALOGNAME="messages"

# List of languages
LANGUAGES="en ca es it"

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po
        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po
    fi
done
