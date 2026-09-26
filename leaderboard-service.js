const config = window.POKE_LEADERBOARD_FIREBASE_CONFIG;
if (!config || !config.apiKey || !config.projectId || !config.appId || !config.authDomain) {
  window.sharedLeaderboardError = 'Shared leaderboard setup is pending.';
  window.dispatchEvent(new Event('sharedLeaderboardReady'));
} else {
  try {
    const version = '12.3.0';
    const [{ initializeApp }, authApi, dbApi] = await Promise.all([
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-app.js`),
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-auth.js`),
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-firestore.js`),
    ]);
    const app = initializeApp(config);
    const auth = authApi.getAuth(app);
    const db = dbApi.getFirestore(app);
    const provider = new authApi.GoogleAuthProvider();
    const modes = new Set(['normal', 'hard', 'chill']);
    const scoresRef = mode => {
      if (!modes.has(mode)) throw new Error('Invalid leaderboard mode');
      return dbApi.collection(db, 'leaderboards', mode, 'scores');
    };
    window.sharedLeaderboard = {
      user: () => auth.currentUser,
      async signIn() {
        if (auth.currentUser) return auth.currentUser;
        const result = await authApi.signInWithPopup(auth, provider);
        return result.user;
      },
      async list(mode) {
        const q = dbApi.query(scoresRef(mode), dbApi.orderBy('score', 'desc'), dbApi.limit(5));
        const snapshot = await dbApi.getDocs(q);
        return snapshot.docs.map(doc => ({ name: doc.data().name, score: doc.data().score }));
      },
      async submit(mode, name, score) {
        if (!auth.currentUser || !modes.has(mode) || !Number.isSafeInteger(score) || score <= 0 || name.length < 1 || name.length > 20) throw new Error('Invalid score');
        const ref = dbApi.doc(scoresRef(mode), auth.currentUser.uid);
        return dbApi.runTransaction(db, async transaction => {
          const previous = await transaction.get(ref);
          if (previous.exists() && previous.data().score >= score) return previous.data().score === score ? 'equal' : 'lower';
          transaction.set(ref, { name, score, updatedAt: dbApi.serverTimestamp() });
          return 'posted';
        });
      },
    };
    window.dispatchEvent(new Event('sharedLeaderboardReady'));
  } catch (e) {
    window.sharedLeaderboardError = 'Could not connect to the shared leaderboard.';
    window.dispatchEvent(new Event('sharedLeaderboardReady'));
  }
}
