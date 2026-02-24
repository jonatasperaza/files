import { ref as p, computed as g } from "vue";
function v(e, u, s) {
  e.defaults.withCredentials = !0, e.defaults.baseURL = u.baseURL;
  let o = !1, t = [];
  const c = (n, l) => {
    t.forEach(
      ({ resolve: i, reject: r }) => n ? i() : r(l)
    ), t = [];
  };
  e.interceptors.response.use(
    // Resposta OK — passa direto
    (n) => n,
    async (n) => {
      var i;
      const l = n.config;
      if (((i = n.response) == null ? void 0 : i.status) !== 401 || l._retried)
        return Promise.reject(n);
      if (o)
        return new Promise((r, d) => {
          t.push({
            resolve: () => r(e(l)),
            reject: d
          });
        });
      l._retried = !0, o = !0;
      try {
        return await e.post(u.refreshEndpoint), c(!0), e(l);
      } catch (r) {
        return c(!1, r), s(), Promise.reject(r);
      } finally {
        o = !1;
      }
    }
  );
}
const f = p(null), a = p(!1), h = p(null), w = g(() => f.value !== null);
function m(e, u) {
  async function s(n) {
    var l, i;
    a.value = !0, h.value = null;
    try {
      await e.post(u.loginEndpoint, n), await t();
    } catch (r) {
      const d = ((i = (l = r == null ? void 0 : r.response) == null ? void 0 : l.data) == null ? void 0 : i.detail) ?? "Erro ao realizar login.";
      throw h.value = d, r;
    } finally {
      a.value = !1;
    }
  }
  async function o() {
    a.value = !0, h.value = null;
    try {
      await e.post(u.logoutEndpoint);
    } catch {
    } finally {
      f.value = null, a.value = !1;
    }
  }
  async function t() {
    a.value = !0;
    try {
      const n = await e.get(u.userEndpoint);
      f.value = n.data;
    } catch {
      f.value = null;
    } finally {
      a.value = !1;
    }
  }
  async function c() {
    await e.post(u.refreshEndpoint);
  }
  return {
    // Estado
    user: f,
    isAuthenticated: w,
    isLoading: a,
    error: h,
    // Ações
    login: s,
    logout: o,
    fetchUser: t,
    refresh: c
  };
}
const y = {
  loginEndpoint: "/auth/login/",
  logoutEndpoint: "/auth/logout/",
  refreshEndpoint: "/auth/refresh/",
  userEndpoint: "/auth/me/",
  loginRoute: "/login"
};
function R(e, u) {
  const s = { ...y, ...u };
  return {
    install(o) {
      let t = null;
      v(e, s, () => {
        t ? t.push(s.loginRoute) : window.location.href = s.loginRoute;
      }), o.provide("cookieJwtAxios", e), o.provide("cookieJwtOptions", s), o.mixin({
        beforeCreate() {
          !t && this.$router && (t = this.$router);
        }
      });
    }
  };
}
export {
  R as createCookieJwt,
  m as useAuth
};
