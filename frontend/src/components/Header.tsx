"use client";

import { Search, Bell, ChevronDown, Shield } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { SignedIn, SignedOut, UserButton, SignInButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

const navItems = ["Dashboard", "Projects", "Reports", "Rules", "Settings"];

import { useUser } from "@clerk/nextjs";

export function Header() {
    const { user } = useUser();

    return (
        <header className="h-16 border-b bg-card px-6 flex items-center justify-between">
            <div className="flex items-center gap-8">
                {/* Logo */}
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                        <Shield className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <span className="font-semibold text-lg text-foreground">SecureScript</span>
                </div>
            </div>

            <div className="flex items-center gap-4">
                {/* Search */}
                <div className="relative hidden md:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        placeholder="Search repositories..."
                        className="w-64 pl-9 bg-muted/50 border-transparent focus:border-border focus:bg-card"
                    />
                </div>

                {/* Notifications */}
                <button className="relative p-2 rounded-md hover:bg-muted transition-colors">
                    <Bell className="w-5 h-5 text-muted-foreground" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent rounded-full" />
                </button>

                {/* User */}
                <SignedOut>
                    <SignInButton mode="modal">
                        <Button size="sm">Sign In</Button>
                    </SignInButton>
                </SignedOut>
                <SignedIn>
                    <div className="flex items-center gap-3 pl-2 pr-1 py-1">
                        <span className="text-sm font-medium hidden sm:inline text-foreground">
                            {user?.fullName || user?.firstName || 'User'}
                        </span>
                        <UserButton afterSignOutUrl="/" />
                    </div>
                </SignedIn>
            </div>
        </header>
    );
}
