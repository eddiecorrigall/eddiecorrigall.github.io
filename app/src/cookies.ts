export const setCookie = (name: string, value: string): void => {
  document.cookie = `${name}=${value}`;
};

export const getCookie = (name: string): string | undefined => {
  // https://www.w3schools.com/js/js_cookies.asp
  const start = name + '=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
          c = c.substring(1);
      }
      if (c.indexOf(start) == 0) {
          return c.substring(start.length, c.length);
      }
  }
  return undefined;
}
