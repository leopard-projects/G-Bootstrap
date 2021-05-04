import { DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Promotion } from 'w-brew';
import {
          CardModel,
          Image,
          ContentModel
       } from 'w-brew';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-linktest',
  templateUrl: './linktest.component.html',
  styleUrls: ['./linktest.component.scss']
})
export class LinktestComponent implements OnInit {
  promotion?: Promotion;
  horizontalCardOne? : CardModel;
  horizontalCardTwo?: CardModel;
  fullCardOne?: CardModel;
  fullCardTwo?: CardModel;
  notificationVarition?: string = 'primary';
  notificationText?: string = '9+';

  students = {
    dob: ''
  }

  constructor(private store: Store<{promotion: {promotion: Promotion}}>) { }

  checkDate() {
    const dateSendingToServer = new DatePipe('en-US').transform(this.students.dob, 'dd/MM/yyyy')
    console.log('dateSendingToServer :', dateSendingToServer);
  }

  ngOnInit(): void {
    this.store.select('promotion').subscribe(data => {
      this.promotion = data.promotion;
      this.promotion = ( this.promotion
        && Object.keys(this.promotion).length === 0
        && this.promotion.constructor === Object ) ? undefined : this.promotion;
    });

    const imageOne = new Image(environment.api.jeans, 'Tapper Jeans');
    const contentOne = new ContentModel(undefined, 'Card title', 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.', false, 'Last updated 3 mins ago');

    this.horizontalCardOne = new CardModel(imageOne, contentOne);

    const imageTwo = new Image(environment.api.jeans, 'Tapper Jeans');
    const contentTwo = new ContentModel(undefined, 'Card title', 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.', true, 'Last updated 3 mins ago');

    this.horizontalCardTwo = new CardModel(imageTwo, contentTwo);

    const imageFullOne = new Image(environment.api.computer, 'Mac to Work.');
    const contentFullOne = new ContentModel(undefined, 'Card title', 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.', false, 'Last updated 3 mins ago');

    this.fullCardOne = new CardModel(imageFullOne, contentFullOne);

    const imageFullTwo = new Image(environment.api.stage, 'My Computer Desk');
    const contentFullTwo = new ContentModel(undefined, 'Card title', 'This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.', true, 'Last updated 3 mins ago');

    this.fullCardTwo = new CardModel(imageFullTwo, contentFullTwo);



  }

}
