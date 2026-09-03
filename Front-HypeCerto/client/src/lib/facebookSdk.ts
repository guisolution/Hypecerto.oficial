// client/src/lib/facebookSdk.ts
//
// Utilitário para carregar o Facebook JS SDK e disparar o login OAuth
// usado para conectar Páginas do Facebook e contas Instagram Business.
//
// Requer a variável de ambiente VITE_META_APP_ID (App ID criado em
// developers.facebook.com/apps).

declare global {
  interface Window {
    FB?: any;
    fbAsyncInit?: () => void;
  }
}

const META_APP_ID = import.meta.env.VITE_META_APP_ID as string | undefined;
const META_API_VERSION = (import.meta.env.VITE_META_API_VERSION as string) || "v18.0";

// Permissões necessárias para listar Páginas, ler a conta Instagram
// vinculada e publicar conteúdo.
const LOGIN_SCOPE = [
  "pages_show_list",
  "pages_manage_posts",
  "pages_read_engagement",
  "instagram_basic",
  "instagram_content_publish",
].join(",");

let sdkLoadPromise: Promise<void> | null = null;

/**
 * Carrega o script do Facebook SDK uma única vez e inicializa o FB.init().
 */
export function loadFacebookSdk(): Promise<void> {
  if (sdkLoadPromise) return sdkLoadPromise;

  sdkLoadPromise = new Promise((resolve, reject) => {
    if (!META_APP_ID) {
      reject(
        new Error(
          "VITE_META_APP_ID não configurado. Defina essa variável no .env do frontend."
        )
      );
      return;
    }

    if (window.FB) {
      resolve();
      return;
    }

    window.fbAsyncInit = function () {
      window.FB!.init({
        appId: META_APP_ID,
        cookie: true,
        xfbml: false,
        version: META_API_VERSION,
      });
      resolve();
    };

    const script = document.createElement("script");
    script.src = "https://connect.facebook.net/pt_BR/sdk.js";
    script.async = true;
    script.defer = true;
    script.crossOrigin = "anonymous";
    script.onerror = () => reject(new Error("Falha ao carregar o SDK do Facebook."));
    document.body.appendChild(script);
  });

  return sdkLoadPromise;
}

export interface FacebookLoginResult {
  accessToken: string;
}

/**
 * Abre o popup de login do Facebook e resolve com o Access Token de
 * curta duração do usuário, já solicitando as permissões necessárias.
 *
 * IMPORTANTE: para o navegador não bloquear o popup, o SDK precisa já
 * estar carregado ANTES do clique (chame loadFacebookSdk() cedo, ex:
 * num useEffect ao montar a página). Esta função assume que já está
 * carregado e chama FB.login() de forma síncrona dentro do handler de
 * clique — sem nenhum `await` antes dela.
 */
export function loginComFacebook(): Promise<FacebookLoginResult> {
  if (!window.FB) {
    return Promise.reject(
      new Error(
        "O SDK do Facebook ainda não carregou. Aguarde alguns segundos e tente novamente."
      )
    );
  }

  return new Promise((resolve, reject) => {
    window.FB.login(
      (response: any) => {
        if (response.authResponse?.accessToken) {
          resolve({ accessToken: response.authResponse.accessToken });
        } else {
          reject(new Error("Login cancelado ou permissões não concedidas."));
        }
      },
      { scope: LOGIN_SCOPE }
    );
  });
}