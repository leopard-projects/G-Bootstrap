import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'lib-notification',
  templateUrl: './notification.component.html',
  styleUrls: ['./notification.component.scss']
})
export class NotificationComponent implements OnInit {
  @Input() variation?: string;
  @Input() labelText?: string;
  constructor() { }

  ngOnInit(): void {
    console.log('variation : ', this.variation);
    console.log('labelText : ', this.labelText);
    console.log('condition : ', (this.variation && this.variation === 'primary'));

  }

}
