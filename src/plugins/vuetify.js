import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'  
import { VDateInput } from 'vuetify/labs/VDateInput'  // ← Import du composant Labs
import 'vuetify/styles'

export default createVuetify({
  components: {
    ...components,
    VDateInput,  // ← Ajout du composant Labs à la configuration
  },
  defaultTheme: 'dark',
  themes: {
    light: {
      dark: false,
      colors: {
        background: '#AAAAAA',
        surface: '#FFFFFF',
        primary: '#1976D2',
        // autres couleurs...
      },
    },
    dark: {
      dark: true,
      colors: {
        background: '#121212',
        surface: '#1E1E1E',
        primary: '#90CAF9',
        // autres couleurs...
      },
    },
  },
  directives,
  icons: {
    defaultSet: 'mdi',
  },
})
