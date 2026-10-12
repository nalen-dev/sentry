import { isWebTarget } from './data';

/**
 * Route prefix for the main application.
 * - Web (cloud): the SCADA app lives under `/app` (marketing site owns `/`, `/docs`, `/login`).
 * - Desktop (Tauri): unchanged, app lives at the root.
 */
export const APP_BASE = isWebTarget ? '/app' : '';

/** Build an in-app route, e.g. appPath('/chart') -> '/app/chart' (web) or '/chart' (desktop). */
export const appPath = (p: string = ''): string => {
  const path = p === '/' ? '' : p;
  return `${APP_BASE}${path}` || '/';
};

/** Route of the post-login launcher page (web only). */
export const MAIN_PATH = '/main';

/** Where the user lands right after logging in. */
export const POST_LOGIN_PATH = isWebTarget ? MAIN_PATH : '/';

/** Send the user to the login page. Web uses the static site's /login (full page load). */
export const goToLogin = (navigate?: (to: string, opts?: any) => void) => {
  if (isWebTarget) {
    window.location.assign('/login');
  } else if (navigate) {
    navigate('/login');
  }
};
