import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PromotionhookComponent } from './promotionhook.component';

describe('PromotionhookComponent', () => {
  let component: PromotionhookComponent;
  let fixture: ComponentFixture<PromotionhookComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PromotionhookComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PromotionhookComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
