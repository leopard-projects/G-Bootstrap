import { Image } from "./image.model";

export class Carousel {
  constructor(
    public image: Image,
    public isActive?: boolean,
    public headingText?: string,
    public subheadingText?: string) {}
}
