import {
        Component,
        EventEmitter,
        Input,
        OnInit,
        Output
      } from'@angular/core';
import {
        FormControl,
        FormGroup,
        Validators
      } from '@angular/forms';

import { Promotion } from '../../models/promotion.model';
import { PromotionService } from '../../services/promotion.service';

@Component({
  selector: 'lib-promotion',
  templateUrl: './promotion.component.html',
  styleUrls: ['./promotion.component.scss']
})
export class PromotionComponent implements OnInit {

  @Input() promotion?: Promotion;
  @Output() otPromotion: EventEmitter<Promotion> = new EventEmitter<Promotion>()
  promotionForm: FormGroup = new FormGroup({});
  keys: string[] = [];

  constructor(
    private promotionService: PromotionService
  ) { }

  ngOnInit(): void {
    const controlConfiguration = this.promotion?.controlConfiguration;

    if (controlConfiguration) {
      this.keys = Object.keys(controlConfiguration)

      this.keys.forEach(item => {
        this.promotionForm.addControl(item, new FormControl(null, [Validators.required]))
      });

    }
  }

  onSubmit(): void {
    const user: {[key: string]: string} = {
      email: this.promotionForm.get('email')?.value,
      name: this.promotionForm.get('name')?.value
    }
    const promotionObject: Promotion = {
        ...this.promotion
      }
    if (promotionObject && promotionObject.controlConfigurationValues) {
        promotionObject.controlConfigurationValues = user;
        promotionObject.isRegistered = true;
    }
    this.otPromotion.emit(promotionObject);
    this.promotionForm.reset();
  }
}
