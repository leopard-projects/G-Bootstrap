import { ContentModel } from './content.model';
import { Image } from './image.model';

export class FullWideModel {
  constructor(
    public image?: Image,
    public content?: ContentModel,
    public listHeading?: ContentModel,
    public listOne?: string[],
    public listTwo?: string[]
    ) {
  }
}
