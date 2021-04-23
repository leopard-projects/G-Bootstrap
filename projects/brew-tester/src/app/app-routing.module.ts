import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DemoComponent } from './components/demo/demo.component';
import { LinktestComponent } from './components/linktest/linktest.component';

const routes: Routes = [
  {
    path: '',
    component: DemoComponent
  },
  {
    path: 'aboutus',
    component: LinktestComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
