import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { ActivatedRoute, Router } from '@angular/router';

import {
  NavigationModel,
  LinkModel
} from 'w-brew';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent implements OnInit {
  navigation?: NavigationModel;
  isPromotionToDisplay: boolean = true;
  constructor(
    private titleService: Title,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.setTitle('Home - Web Brew');
  }

  ngOnInit(): void {
    console.log(this.router.url);

    const linkModel: LinkModel[] = [];
    const linkOne = new LinkModel('Home', 'Home' ,true, undefined);
    linkModel.push(linkOne);

    const linkTwo = new LinkModel('Advisor', 'Advisor',  false, undefined);
    linkModel.push(linkTwo);

    // const linkThree = new LinkModel('Planner','Planner' , false, undefined);
    // linkModel.push(linkThree);

    // const linkFour = new LinkModel('Contact Us', 'Contactus', false, undefined);
    // linkModel.push(linkFour);

    // const linkFive = new LinkModel('About Us', 'Aboutus' , false, undefined);
    // linkModel.push(linkFive);

    this.navigation = new NavigationModel('Start.up', '', linkModel);
  }

  public setTitle(newTitle: string): void {
    this.titleService.setTitle(newTitle);
  }

  triggeredNavigation(link: LinkModel) {
    let links : LinkModel[] = this.navigation?.links && this.navigation?.links.length > 0 ? this.navigation?.links: [];

    links.map(element => {
      if (element.routerName === link.routerName) {
        element.isActive = true;
      } else {
        element.isActive = false;
      }
    });

    if (link?.routerName) {
      this.isPromotionToDisplay = (link?.routerName === 'Home') ? true : false;
      this.router.navigateByUrl(link?.routerName).then( (e) => {
        if ( e ) {
          console.log("Navigation is successful!");
        } else {
          console.log("Navigation has failed!" , e);
        }
      });
    }

  }
}



    // const observer = {
    //   next: (promotion: Promotion) => {
    //     this.promotion = promotion;
    //   },
    //   error: (error: Error) => {
    //     console.log('Promotion Fallback...');
    //   },
    //   complete: () => {
    //     console.log('completed the process ...');
    //   }
    // }


    // this.promotionService.loadPromotion().subscribe(observer);
