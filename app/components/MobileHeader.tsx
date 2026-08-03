export default function MobileHeader() {
  return (
    <header className="desk:hidden flex flex-col gap-2 px-5 pt-5 pb-4 border-b border-ink/[0.14]">
      <div className="motif-band h-2" aria-hidden="true" />
      <div className="flex items-baseline justify-between">
        <h1 className="m-0 font-serif font-bold text-[26px]">Achalugo</h1>
        <span className="text-[10px] tracking-[.2em] uppercase text-terracotta">
          Onye Amamihe
        </span>
      </div>
    </header>
  );
}
