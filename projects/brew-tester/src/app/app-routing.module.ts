import { NgModule } from "@angular/core";
import { Routes, RouterModule } from "@angular/router";
import { DemoComponent } from "./components/demo/demo.component";
import { LinktestComponent } from "./components/linktest/linktest.component";
import { PagenotfoundComponent } from "w-brew";

const routes: Routes = [
  {
    path: "Home",
    component: DemoComponent,
  },
  {
    path: "Advisor",
    component: LinktestComponent,
  },
  {
    path: "Planner",
    component: LinktestComponent,
  },
  {
    path: "Contactus",
    component: LinktestComponent,
  },
  {
    path: "Aboutus",
    component: LinktestComponent,
  },
  {
    path: "",
    redirectTo: "/Home",
    pathMatch: "full",
  },
  {
    path: "**",
    component: PagenotfoundComponent,
  }, // PageNotFoundComponent TO-DO
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule],
})
export class AppRoutingModule {}

// {   path: '',
//       redirectTo: 'home/home',
//       pathMatch: 'full',
//   },
//   {
//       path: 'home/:name',
//       component: DyanamicloaderComponent
//   },
//   {
//     path: 'about/:name',
//     component: DyanamicloaderComponent
//   },
//   {
//     path: 'portfolio/:name',
//     component: DyanamicloaderComponent
//   },
//   {
//     path: 'faqs/:name',
//     component: DyanamicloaderComponent
//   },
//   {
//     path: 'links/:name',
//     component: DyanamicloaderComponent
//   },
//   {
//     path: 'contact/:name',
//     component: DyanamicloaderComponent
//   }
