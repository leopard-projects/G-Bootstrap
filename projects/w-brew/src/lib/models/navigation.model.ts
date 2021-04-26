import { LinkModel } from "./link.model";

export class NavigationModel {
  constructor(
    public title?: string,
    public logoUrl?: string,
    public links?: LinkModel[]
  ) {}
}
