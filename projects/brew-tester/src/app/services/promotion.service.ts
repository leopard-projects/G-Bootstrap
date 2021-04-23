import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Promotion } from 'w-brew';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PromotionService {

  constructor(
    private http: HttpClient
  ) { }

  loadPromotion(): Observable<Promotion> {
    const promotionUrl = environment.api.promotion;
    return this.http.get(promotionUrl);
  }
}
