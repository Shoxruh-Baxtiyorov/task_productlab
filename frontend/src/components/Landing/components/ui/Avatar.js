import React from 'react';

const colorBg = ["bg-indigo-600", "bg-emerald-600", "bg-rose-600", "bg-amber-600"];

const Avatar = ({ initials, i }) => {
  const bg = colorBg[i % colorBg.length];
  
  return (
    <div
      className={`inline-flex h-12 w-12 select-none items-center justify-center rounded-full font-semibold text-white ${bg} shadow-sm`}
      aria-hidden="true"
    >
      {initials}
    </div>
  );
};

export default Avatar;
