import { useState } from "react";

export default function AccountMenu() {
    const [open, setOpen] = useState(false);

    const email =
        localStorage.getItem("user_email") || "Not available";

    const name =
        localStorage.getItem("user_name") || "User";

    function handleReports() {
        alert("Reports feature will open here.");
    }

    function handleLogout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_name");
        localStorage.removeItem("user_email");
        localStorage.removeItem("user_role");

        window.location.reload();
    }

    return (
        <div className="relative">

            {/* Account Button */}
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2 rounded-xl bg-neutral-800 px-4 py-2 text-white hover:bg-neutral-700"
            >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600">
                    {name.charAt(0).toUpperCase()}
                </span>

                <span className="hidden sm:block">
                    My Account
                </span>

                <span>
                    {open ? "▲" : "▼"}
                </span>
            </button>

            {/* Dropdown */}
            {open && (
                <div className="absolute right-0 z-50 mt-2 w-80 rounded-2xl border border-neutral-700 bg-neutral-900 p-4 shadow-2xl">

                    {/* User Information */}
                    <div className="border-b border-neutral-700 pb-4">

                        <p className="text-sm text-neutral-400">
                            Account
                        </p>

                        <p className="mt-1 font-semibold text-white">
                            {name}
                        </p>

                        <p className="text-sm text-neutral-300">
                            {email}
                        </p>

                    </div>

                    {/* Balance */}
                    <div className="border-b border-neutral-700 py-4">

                        <p className="text-sm text-neutral-400">
                            Account Balance
                        </p>

                        <p className="mt-1 text-2xl font-bold text-green-400">
                            Not available
                        </p>

                        <p className="mt-1 text-xs text-neutral-500">
                            Balance information will be connected to the
                            customer account.
                        </p>

                    </div>

                    {/* Reports */}
                    <div className="py-4">

                        <button
                            type="button"
                            onClick={handleReports}
                            className="w-full rounded-xl bg-blue-600 px-4 py-3 text-left text-white hover:bg-blue-700"
                        >
                            📊 View My Reports
                        </button>

                    </div>

                    {/* Logout */}
                    <button
                        type="button"
                        onClick={handleLogout}
                        className="w-full rounded-xl bg-red-600 px-4 py-3 text-white hover:bg-red-700"
                    >
                        Sign Out
                    </button>

                </div>
            )}

        </div>
    );
}