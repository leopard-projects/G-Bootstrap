import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WideContainerComponent } from './wide-container.component';

describe('WideContainerComponent', () => {
  let component: WideContainerComponent;
  let fixture: ComponentFixture<WideContainerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WideContainerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WideContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
