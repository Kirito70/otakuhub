import { configure } from 'quasar/wrappers'

export default configure((ctx) => {
  const isWebLikeTarget = !(ctx.mode.electron || ctx.mode.capacitor)

  return {
    css: ['app.scss'],
    boot: ['axios', 'theme', 'bootstrap'],
    extras: ['material-icons'],
    build: {
      target: {
        browser: ['esnext'],
        node: 'node20',
      },
      // Use history mode for web targets, hash mode for file-based shells
      // (Electron/Capacitor) to avoid blank-page deep-link issues.
      vueRouterMode: isWebLikeTarget ? 'history' : 'hash',
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
      builder: {
        linux: {
          icon: 'src-electron/icons/icon.png',
        },
      },
    },
  }
})
