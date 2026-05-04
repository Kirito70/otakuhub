import { configure } from 'quasar/wrappers'

export default configure(() => {
  return {
    css: ['app.scss'],
    boot: ['axios', 'theme'],
    extras: ['material-icons'],
    build: {
      target: {
        browser: ['esnext'],
        node: 'node20',
      },
      vueRouterMode: 'hash',
    },
    framework: {
      plugins: ['Notify', 'Dialog', 'Loading', 'Dark'],
    },
    capacitor: {
      appId: 'com.otakuhub.app',
      hideSplashscreen: true,
    },
    electron: {
      bundler: 'builder',
    },
  }
})
