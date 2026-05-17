type Props = {
  code: string;
  label?: string;
};

export function ReferenceCode({ code, label = "Request ID" }: Props) {
  return (
    <p className="reference-code" data-testid="request-reference-code">
      <span className="reference-code__label">{label}</span>{" "}
      <code className="reference-code__value">{code}</code>
    </p>
  );
}
