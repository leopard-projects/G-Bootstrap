// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  production: false,
  api: {
    promotion: "http://localhost:8989/brew/assets/mock-api/promotion.json",
    carousel: "http://localhost:8989/brew/assets/mock-api/carousel.json",
    widecontainerone:
      "http://localhost:8989/brew/assets/mock-api/wide-container-one.json",
    macbook: "http://localhost:8989/brew/assets/images/macbook.png",
    bradelvis: "http://localhost:8989/brew/assets/images/brad-elvis.png",
    ipad: "http://localhost:8989/brew/assets/images/ipad.png",
    macbook2: "http://localhost:8989/brew/assets/images/macbook-2.png",
    jeans: "http://localhost:8989/brew/assets/images/jeans.svg",
    computer: "http://localhost:8989/brew/assets/images/computer.jpg",
    stage: "http://localhost:8989/brew/assets/images/stage.jpg",
  },
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
