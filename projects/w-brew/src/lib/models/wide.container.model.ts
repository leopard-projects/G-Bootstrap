import { ClickToAction } from "./click.to.action.model";
import { ColorModel } from "./color.model";
import { Image } from "./image.model";
import { ContentModel } from './content.model';

export class WideContainerModel {

  constructor(
    public colorModel?: ColorModel,
    public image?: Image,
    public content?: ContentModel,
    public c2a?: ClickToAction
  ) {}

}
