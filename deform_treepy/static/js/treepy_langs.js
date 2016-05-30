
treepyI18n = {
'en': {
  'Rename': 'Rename',
  'Remove': 'Remove',
  "Add a category": "Add a category",
  "- Select -": "- Select -",
 },

'fr':{
  'Rename': 'Renommer',
  'Remove': 'Supprimer',
  "Add a category": "Ajouter une catégorie",
  "- Select -": "- Sélectionner -",
}
}


function treepy_translate(msgid){
      var local = 'fr'//treepy_get_language()
      var msgs = treepyI18n[local]
      if (msgid in msgs){
         return msgs[msgid]
      }

      return msgid
}
