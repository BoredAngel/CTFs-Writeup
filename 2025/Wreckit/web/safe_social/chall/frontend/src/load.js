import frontendJs from './fe.js?url';

var s = document.createElement('script');
s.src = frontendJs;
document.head.append(s);