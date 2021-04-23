import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Promotion } from 'w-brew';

@Component({
  selector: 'app-linktest',
  templateUrl: './linktest.component.html',
  styleUrls: ['./linktest.component.scss']
})
export class LinktestComponent implements OnInit {
  promotion?: Promotion;
  constructor(private store: Store<{promotion: {promotion: Promotion}}>) { }

  ngOnInit(): void {
    this.store.select('promotion').subscribe(data => {
      this.promotion = data.promotion;
      this.promotion = ( this.promotion
        && Object.keys(this.promotion).length === 0
        && this.promotion.constructor === Object ) ? undefined : this.promotion;
    });
  }

}
