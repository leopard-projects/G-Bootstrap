import { TestBed } from '@angular/core/testing';

import { WBrewService } from './w-brew.service';

describe('WBrewService', () => {
  let service: WBrewService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(WBrewService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
