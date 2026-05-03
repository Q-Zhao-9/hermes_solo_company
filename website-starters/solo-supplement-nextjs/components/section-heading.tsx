type SectionHeadingProps = {
  title: string;
  body: string;
};

export function SectionHeading({ title, body }: SectionHeadingProps) {
  return (
    <div className="section-heading">
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}
