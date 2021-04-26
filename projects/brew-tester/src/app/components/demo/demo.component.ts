import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';

import {
  Carousel,
  Promotion,
  WideContainerModel,
  Image,
  ClickToAction,
  ContentModel,
  ColorModel,
  FullWideModel
} from 'w-brew';

import * as CarouselActions from '../../store/carousel/carousel.action';

@Component({
  selector: 'app-demo',
  templateUrl: './demo.component.html',
  styleUrls: ['./demo.component.scss']
})
export class DemoComponent implements OnInit {

  promotionData?: Observable<{ promotion: Promotion }>;
  promotion?: Promotion;
  carousel?: Carousel[] = [];
  wideContainer?: WideContainerModel;
  middleWideContainer?: WideContainerModel;
  bottomWideContainer?: WideContainerModel;
  fullWideContainer?: FullWideModel;

  constructor(
    private store: Store<{
      promotion: {promotion: Promotion},
      carousel: {slides: Carousel[]}
    }>) {
      // this.store.dispatch(new PromotionActions.FetchPromotion());
      // this.store.dispatch(new CarouselActions.FetchCarousel());
    }

  ngOnInit(): void {

    this.store.select('carousel').subscribe((response: { slides: Carousel[] }) => {
      if (response && response.slides && response.slides.length > 0 ) {
        this.carousel = response.slides;
      } else {
        this.store.dispatch(new CarouselActions.FetchCarousel());
      }
    });

    let colorModel = new ColorModel('#FFFF', 'black');
    let image = new Image('../../../assets/images/macbook.png', 'macbook');
    let c2a = new ClickToAction('Git\'r done!', 'www.google.com');
    let titleOfHeading = 'The wow factor';
    let title = 'Australians wouldn\'t give a Startup.logo for anything else.';
    let description = 'Lorem, ipsum dolor sit amet consectetur adipisicing elit. Nemo tenetur aliquid veritatis accusantium, nesciunt quo fuga quisquam quod temporibus unde obcaecati amet minus, illo quibusdam! Officia asperiores fugit alias quo. <a href="https://www.google.com/">Go Google</a>';
    let content = new ContentModel(titleOfHeading, title, description, false);
    this.wideContainer = new WideContainerModel(colorModel, image, content, c2a);


    let middleColorModel = new ColorModel('#f0f0f0', 'black');
    let middleImage = new Image('../../../assets/images/brad-elvis.png', 'iPad');
    let middleC2a = new ClickToAction('Mangos!(or mangoes?)', 'www.google.com');
    let middleTitleOfHeading = 'Kudos';
    let middleTitle = '\"No Startup.logo, no kiss.\"';
    let middleDescription = '-Brelvis Hesley, some guy at a wedding.';
    let middleContent = new ContentModel(middleTitleOfHeading, middleTitle, middleDescription, true);
    this.middleWideContainer = new WideContainerModel(middleColorModel, middleImage, middleContent, undefined);


    let bottomColorModel = new ColorModel('black', 'white');
    let bottomImage = new Image('../../../assets/images/ipad.png', 'iPad');
    let bottomC2a = new ClickToAction('Mangos!(or mangoes?)', 'www.google.com');
    let bottomTitleOfHeading = 'The all-in-one solution';
    let bottomTitle = 'Nobody doesn\'t like Startup.logo';
    let bottomDescription = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Tempora quo corporis sapiente necessitatibus, blanditiis pariatur assumenda perferendis? Minima, debitis alias cumque reprehenderit quo exercitationem temporibus iusto beatae, nam et maiores!';
    let bottomContent = new ContentModel(bottomTitleOfHeading, bottomTitle, bottomDescription, true);
    this.bottomWideContainer = new WideContainerModel(bottomColorModel, bottomImage, bottomContent, bottomC2a);


    let wideColorModel = new ColorModel('black', 'white');
    let wideImage = new Image('../../../assets/images/macbook-2.png', 'Macbook...');

    let wideTitleOfHeading = 'Powerfully packed action';
    let wideTitle = 'When it absolutely, positively has to be Startup.logo overnight.';
    let wideDescription = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Ex culpa alias consequatur eligendi accusamus? Saepe velit quae porro hic id, quidem soluta beatae, in quis voluptate earum necessitatibus quod rem??';

    let wideContent = new ContentModel(wideTitleOfHeading, wideTitle, wideDescription, false);

    let wideListHeading = new ContentModel(undefined, 'With startup.log you can:', undefined, false);

    let listOne: string[] = [];
    listOne.push('Put Sriracha on just about anything');
    listOne.push('Use your wallet for everything other than buying things');

    let listTwo: string[] = [];
    listTwo.push('Get solid advice from mildy attractive people');
    listTwo.push('win at most things');

    this.fullWideContainer = new FullWideModel(wideImage, wideContent, wideListHeading, listOne, listTwo);

    // console.log('this.bottomWideContaine : ', this.bottomWideContainer);

  }
}
