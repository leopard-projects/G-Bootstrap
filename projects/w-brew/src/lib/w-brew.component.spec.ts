import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WBrewComponent } from './w-brew.component';

describe('WBrewComponent', () => {
  let component: WBrewComponent;
  let fixture: ComponentFixture<WBrewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WBrewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WBrewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
