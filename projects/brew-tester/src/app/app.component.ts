import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {
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
